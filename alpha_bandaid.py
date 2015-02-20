import pygame
import sys



def average_color(colors):
    """Alpha-weighted average of one or more colors."""
    if len(colors) == 0: return (0,0,0,0)
    return tuple(sum(color[n] * color[3] for color in colors) / sum(color[3] for color in colors) for n in range(4))


def main():
    if len(sys.argv) < 2:
        print "Usage: python -m alpha_bandaid input_file (output_file)"
        print "If no output file is specified, the input file will be edited in place"
        sys.exit()

    input_file = sys.argv[1]

    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = input_file

    image = pygame.image.load(input_file)
    w = image.get_width()
    h = image.get_height()

    results = {}
    searching = {}
    colored = {}

    # pre-processing: find all non-transparent pixels in this image
    for x in xrange(w):
        for y in xrange(h):
            if image.get_at((x,y))[3] > 0:
                # don't save this pixel if it isn't surrounded by opaque pixels
                if ((x == 0 or image.get_at((x-1, y))[3] > 0) and
                    (y == 0 or image.get_at((x, y-1))[3] > 0) and
                    (x == w-1 or image.get_at((x+1, y))[3] > 0) and
                    (y == h-1 or image.get_at((x, y+1))[3] > 0)):
                    continue

                # this is a colored edge pixel; save it in the dictionary
                colored[x,y] = image.get_at((x,y))

    colored_pos = colored.keys()

    def closest_color(x, y):
        """Find the value of the closest opaque pixel to position (x, y)"""

        searching[x,y] = True
        if x < 0 or x >= w: return None
        elif y < 0 or y >= h: return None
        elif (x,y) in results: return results[x,y]
        elif image.get_at((x,y))[3] > 0: return image.get_at((x,y))
        else:
            # sort colored pixels by distance
            dist = [(xi, yi, abs(x-xi) + abs(y-yi)) for (xi,yi) in colored_pos]
            dist.sort(key=lambda d: d[2])
            min_dist = dist[0][2]
            colors = []

            # find all pixels tied for minimum distance
            for n in range(len(dist)):
                if not dist[n][2] == min_dist:
                    break
                colors.append(colored[dist[n][0], dist[n][1]])

            # if there are multiple pixels tied for distance, average them
            results[x,y] = average_color(colors)
            return results[x,y]

    for x in xrange(w):
        for y in xrange(h):
            if image.get_at((x,y))[3] == 0:
                # transparent pixel, fill with closest color
                c = closest_color(x,y)
                image.set_at((x, y), (c[0], c[1], c[2], 0))
        msg = '%s%% complete' % round((float(x + 1) / w) * 100, 1)
        sys.stdout.write(('%20s' % msg) + '\b'*20)
        sys.stdout.flush()

    pygame.image.save(image, output_file)


if __name__ == '__main__':
    main()

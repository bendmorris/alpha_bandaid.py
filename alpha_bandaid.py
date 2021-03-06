import argparse
import pygame
import sys
from scipy import spatial


def average_color(colors):
    """Alpha-weighted average of one or more colors."""
    if len(colors) == 0: return (0,0,0,0)
    return tuple(sum(color[n] * color[3] for color in colors) / sum(color[3] for color in colors) for n in range(4))


def main():
    parser = argparse.ArgumentParser(description='alpha_bandaid')
    parser.add_argument('input_file', help='file to clean')
    parser.add_argument('output_file', nargs='?', default=None, help='output file path (none to edit in place)')
    parser.add_argument('--alpha', '-a', type=int, default=0, help='alpha (0-255, default 0)')

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file if args.output_file else input_file
    alpha = args.alpha

    print '%s -> %s' % (input_file, output_file)

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
                # don't save this pixel if it is surrounded by opaque pixels
                if ((x == 0 or image.get_at((x-1, y))[3] > 0) and
                    (y == 0 or image.get_at((x, y-1))[3] > 0) and
                    (x == w-1 or image.get_at((x+1, y))[3] > 0) and
                    (y == h-1 or image.get_at((x, y+1))[3] > 0)):
                    continue

                # this is a colored edge pixel; save it in the dictionary
                colored[x,y] = image.get_at((x,y))

    if not colored:
        pygame.image.save(image, output_file)
        print 'Done'
        return

    colored_pos = colored.keys()
    tree = spatial.KDTree(colored_pos, leafsize=min(w*h/1000, 64))

    def closest_color(x, y):
        """Find the value of the closest opaque pixel to position (x, y)"""

        searching[x,y] = True
        if x < 0 or x >= w: return None
        elif y < 0 or y >= h: return None
        elif (x,y) in results: return results[x,y]
        elif image.get_at((x,y))[3] > 0: return image.get_at((x,y))
        else:
            # find closest colored pixels
            closest = tree.query([(x, y)], p=1)
            min_dist = closest[0][0]
            colors = []
            for distance, index in zip(closest[0], closest[1]):
                if distance > min_dist: break
                xi, yi = colored_pos[index]
                colors.append(colored[xi, yi])

            # if there are multiple pixels tied for distance, average them
            results[x,y] = average_color(colors)
            return results[x,y]

    for x in xrange(w):
        for y in xrange(h):
            if image.get_at((x,y))[3] == 0:
                # transparent pixel, fill with closest color
                c = closest_color(x,y)
                image.set_at((x, y), (c[0], c[1], c[2], alpha))
        msg = '%s%% complete' % round((float(x + 1) / w) * 100, 1)
        sys.stdout.write(('%20s' % msg) + '\b'*20)
        sys.stdout.flush()

    pygame.image.save(image, output_file)
    print '\nDone'


if __name__ == '__main__':
    main()

import pygame
import sys



def average_color(colors):
    if len(colors) == 0: return (0,0,0,0)
    return tuple([sum(color[n] for color in colors) / len(colors) for n in range(4)])


def main():
    if len(sys.argv) < 2:
        print "Usage: python -m alpha_bandaid.py input_file (output_file)"
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
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.set_alpha(True)

    results = {}
    searching = {}
    colored = {}


    for x in xrange(w):
        for y in xrange(h):
            if image.get_at((x,y))[3] > 0:
                colored[x,y] = image.get_at((x,y))

    colored_pos = colored.keys()

    def closest_color(x, y):
        searching[x,y] = True
        if x < 0 or x >= w: return None
        elif y < 0 or y >= h: return None
        elif (x,y) in results: return results[x,y]
        elif image.get_at((x,y))[3] > 0: return image.get_at((x,y))
        else:
            dist = [(xi, yi, abs(x-xi) + abs(y-yi)) for (xi,yi) in colored_pos]
            dist.sort(key=lambda d: d[2])
            min_dist = dist[0][2]
            colors = []
            n = 0
            while dist[n][2] == min_dist:
                colors.append(colored[dist[n][0], dist[n][1]])
                n += 1
            results[x,y] = average_color(colors)
            return results[x,y]

    for x in xrange(w):
        for y in xrange(h):
            if image.get_at((x,y))[3] == 0:
                c = closest_color(x,y)
                surf.set_at((x, y), (c[0], c[1], c[2], 0))
            else:
                surf.set_at((x, y), image.get_at((x, y)))

    pygame.image.save(surf, output_file)


if __name__ == '__main__':
    main()

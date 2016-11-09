# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.


def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1x == p2x:
                        inside = not inside
                    else:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if x <= xinters:
                            inside = not inside

        p1x, p1y = p2x, p2y
    return inside


if __name__ == '__main__':
    print(point_inside_polygon(5, 5, [(4, 6), (4, 4), (6, 4), (6, 6), (4, 6)]))

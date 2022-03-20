import img, shapes, ppmIO

p = [shapes.Ellipse((100, 100), (20, 25), fill=(10, 10, 10)), shapes.Line((0,0),(200,200))]
q = [shapes.Polygon([(4,4),(105,29), (185, 215), (10, 100)], fill=(255,0,0)),\
        ppmIO.Picture('cat.ppm', anchor=(150,150))]
im = img.draw_img(801, 801, p, (0,0,255))
im2 = img.draw_img(801, 801, q, (0,0,255))
img.save_img([im, im2],'shape_test.gif')
img.show_img([im, im2], duration=1000)

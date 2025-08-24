import qrcode
import qrcode.image.svg



urlslist=["https://ulkemyanimda.eba.gov.tr/videolar/seviye8/01/index.html",

"https://ulkemyanimda.eba.gov.tr/videolar/seviye8/02/index.html",
"https://ulkemyanimda.eba.gov.tr/videolar/seviye8/03/index.html",
"https://ulkemyanimda.eba.gov.tr/videolar/seviye8/04/index.html",


"https://ulkemyanimda.eba.gov.tr/videolar/seviye8/05/index.html",

"https://ulkemyanimda.eba.gov.tr/videolar/seviye8/06/index.html",
"https://ulkemyanimda.eba.gov.tr/videolar/seviye8/07/index.html",
"https://ulkemyanimda.eba.gov.tr/videolar/seviye8/08/index.html", 
"https://ulkemyanimda.eba.gov.tr/videolar/seviye5/01/dolmabahce.html"]










method = 'fragment'
if method == 'basic':
    # Simple factory, just a set of rects.
    factory = qrcode.image.svg.SvgImage
elif method == 'fragment':
    # Fragment factory (also just a set of rects)
    factory = qrcode.image.svg.SvgFragmentImage
else:
    # Combined path factory, fixes white space that may occur when zooming
    factory = qrcode.image.svg.SvgPathImage


for u,i in enumerate(urlslist):
    print(i)
    print(u+1)    
    img = qrcode.make(i, image_factory=factory)
    name=f'seviye08-0{u+1}.svg'
    img.save(name)


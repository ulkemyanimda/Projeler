import qrcode
import qrcode.image.svg



urlslist=["https://ulkemyanimda.eba.gov.tr/videolar/seviye1/bib.html",
          "https://ulkemyanimda.eba.gov.tr/videolar/seviye2/bib.html",
          "https://ulkemyanimda.eba.gov.tr/videolar/seviye3/bib.html",
          "https://ulkemyanimda.eba.gov.tr/videolar/seviye4/bib.html",
          "https://ulkemyanimda.eba.gov.tr/videolar/seviye5/bib.html",
          "https://ulkemyanimda.eba.gov.tr/videolar/seviye6/bib.html",
          "https://ulkemyanimda.eba.gov.tr/videolar/seviye7/bib.html",
          "https://ulkemyanimda.eba.gov.tr/videolar/seviye8/bib.html"]










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
    name=f'seviye0{u+1}.svg'
    img.save(name)


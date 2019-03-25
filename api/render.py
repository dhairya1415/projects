from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
import os
from urllib.request import urlopen


def render_to_file(path: str, params: dict, file):
    template = get_template(path)
    html = template.render(params)
    file_name = "{}.pdf".format(file)
    file_path = os.path.join("media/pdf", file_name)
    file_pdf = open(file_path, "wb")
    pisaStatus = pisa.CreatePDF(html, dest=file_pdf)
    file_pdf.close()


# class Render:
#
#     @staticmethod
#     def download(path: str, params: dict):
#         template = get_template(path)
#         html = template.render(params)
#         response = BytesIO()
#         pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
#         if not pdf.err:
#             response =  HttpResponse(response.getvalue(), content_type='application/pdf')
#             response["Content-Disposition"] = 'attachment; filename = "abc.pdf"'
#             return response
#         else:
#             return HttpResponse("Error Rendering PDF", status=400)
#
#     @staticmethod
#     def preview(path: str, params: dict):
#         template = get_template(path)
#         html = template.render(params)
#         x = render_to_file(path, params)
#
#         response = BytesIO()
#         pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
#         if not pdf.err:
#             pdf_file =  HttpResponse(response.getvalue(), content_type='application/pdf')
#             return pdf_file
#         else:
#             return HttpResponse("Error Rendering PDF", status=400)

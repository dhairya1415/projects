from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape, portrait, A4
from reportlab.platypus import Image
from reportlab.lib.units import inch, cm
import csv
import pandas as pd


def import_data(data_file):
    df = pd.read_csv(data_file)
    event_name = df["name"][0]
    event_venue = df["venue"][0]
    no_of_participants = df["number_of_participation"][0]
    event_department = df["department"][0]
    image = df["image"][0]
    image = image.replace("[", "")
    image = image.replace("]", "")
    image = image.replace('"', "")
    image = image.replace('"', "")
    image = image.replace("'", "")
    image = image.replace("'", "")
    image = image.split(",")
    print(type(image))
    event_description = df["description"][0]
    event_date = df["start_date"][0]
    pdf_file_name = event_name + "$" + event_date + ".pdf"
    generate_pdf(
        event_name,
        event_venue,
        no_of_participants,
        event_department,
        image,
        event_description,
        event_date,
        pdf_file_name,
    )


def generate_pdf(
    event_name,
    event_venue,
    no_of_participants,
    event_department,
    image,
    event_description,
    event_date,
    pdf_file_name,
):
    c = canvas.Canvas("media/pdf/{}".format(pdf_file_name), pagesize=portrait(A4))
    c.setFont("Helvetica-Bold", 30, leading=None)
    c.drawCentredString(4.135 * inch, 11.19 * inch, "Report for the Event:")
    c.setFont("Helvetica", 20, leading=None)
    c.drawCentredString(4.135 * inch, 10.69 * inch, event_name + " | " + event_date)
    c.drawCentredString(
        4.135 * inch,
        10.50 * inch,
        "-----------------------------------------------------------",
    )
    c.setFont("Helvetica", 15, leading=None)
    c.drawString(
        0.4 * inch, 9.69 * inch, "Event Department: {}".format(event_department)
    )
    c.drawString(0.4 * inch, 9.19 * inch, "Event Venue: {}".format(event_venue))
    c.drawString(
        0.4 * inch, 8.69 * inch, "No. of participants: {}".format(no_of_participants)
    )
    c.drawString(0.4 * inch, 8.19 * inch, "Event Description:")
    c.setFont("Helvetica", 13, leading=None)
    c.drawString(0.4 * inch, 7.9 * inch, event_description)
    c.setFont("Helvetica", 15, leading=None)
    c.drawString(6 * inch, 2 * inch, "Signature")
    c.drawString(6.25 * inch, 1.7 * inch, "(xyz)")

    # textobject = c.beginText()
    # textobject.setTextOrigin(0.2*inch, 7.69*inch)
    # for line in event_description:
    #     textobject.textLine(line)
    # c.drawText(textobject)

    c.showPage()
    c.setFont("Helvetica", 15, leading=None)
    c.drawString(0.4 * inch, 11.19 * inch, "Images:")
    v_gap = 8.19
    for item in image:
        if v_gap > 0:
            c.drawImage(item, 0.4 * inch, v_gap * inch, width=200, height=200)
            v_gap -= 3
    c.showPage()
    c.save()


# A4 dimensions: 8.27 × 11.69 inches

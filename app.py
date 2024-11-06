from flask import Flask, request, render_template, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
import datetime
import os

app = Flask(__name__)

# Store user inputs
user_data = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Collect user input from the form
    user_data['client_name'] = request.form['client_name']
    user_data['company_name'] = request.form['company_name']
    user_data['contact_number'] = request.form['contact_number']
    user_data['event_name'] = request.form['event_name']
    user_data['event_date'] = request.form['event_date']
    user_data['event_time'] = request.form['event_time']
    user_data['num_attendees'] = request.form['num_attendees']
    user_data['event_location'] = request.form['event_location']
    user_data['event_duration'] = request.form['event_duration']
    user_data['services'] = request.form['services']

    pdf_file = generate_pdf()

    if pdf_file:
        return send_file(pdf_file, as_attachment=True)
    else:
        return "Error generating the PDF.", 500

def generate_pdf():
    client_name = user_data.get('client_name', '')
    company_name = user_data.get('company_name', '')
    contact_number = user_data.get('contact_number', '')
    event_name = user_data.get('event_name', '')
    event_date = user_data.get('event_date', '')
    event_time = user_data.get('event_time', '')
    num_attendees = user_data.get('num_attendees', '')
    event_location = user_data.get('event_location', '')
    event_duration = user_data.get('event_duration', '')
    services = user_data.get('services', '')

    # Generate the overlay PDF
    overlay_pdf = "overlay.pdf"
    c = canvas.Canvas(overlay_pdf, pagesize=letter)

    width, height = letter
    y_start = 640  # Starting Y position
    y_step = 20    # Step between lines
    indent = 40    # Indentation for details
    margin_left = 50  # Margin from the left

    # Title
    c.setFont("Helvetica-Bold", 16)
    title = "Catering Order"
    c.drawCentredString(width / 2.0, height - 130, title)  # Adjusted position
    c.setLineWidth(1)
    c.line(width / 2.0 - 60, height - 105, width / 2.0 + 60, height - 105)  # Adjusted position

    # Set font for section titles
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_left, y_start, "Client Information")

    # Set font for normal text
    c.setFont("Helvetica", 12)
    y_start -= y_step
    c.drawString(margin_left + indent, y_start, f" Client Name: {client_name}")
    y_start -= y_step
    c.drawString(margin_left + indent, y_start, f" Company Name: {company_name}")
    y_start -= y_step
    c.drawString(margin_left + indent, y_start, f" Contact Number: {contact_number}")
    y_start -= y_step

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_left, y_start, "Event Details")

    c.setFont("Helvetica", 12)
    y_start -= y_step
    c.drawString(margin_left + indent, y_start, f" Event Name: {event_name}")
    y_start -= y_step
    c.drawString(margin_left + indent, y_start, f" Event Date: {event_date}")
    y_start -= y_step
    c.drawString(margin_left + indent, y_start, f" Event Time: {event_time}")
    y_start -= y_step
    c.drawString(margin_left + indent, y_start, f" Number of Participants: {num_attendees}")
    y_start -= y_step
    c.drawString(margin_left + indent, y_start, f" Event Location: {event_location}")
    y_start -= y_step
    c.drawString(margin_left + indent, y_start, f" Event Duration: {event_duration}")

    # Additional Services Section
    y_start -= y_step  # Adding space before new section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_left, y_start, "Services")

    c.setFont("Helvetica", 12)
    y_start -= y_step
    c.drawString(margin_left + indent, y_start, f"{services}")

    # Save the PDF
    c.save()

    # Combine the overlay PDF with the letterhead PDF
    letterhead_pdf = "template.pdf"  # Make sure you have a template.pdf file
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_pdf = f"Catering_order_{current_datetime}.pdf"

    try:
        with open(letterhead_pdf, "rb") as letterhead_file, open(overlay_pdf, "rb") as overlay_file:
            letterhead = PdfReader(letterhead_file)
            overlay = PdfReader(overlay_file)

            if len(letterhead.pages) == 0 or len(overlay.pages) == 0:
                raise ValueError("One of the PDFs is empty")

            letterhead_page = letterhead.pages[0]
            overlay_page = overlay.pages[0]

            letterhead_page.merge_page(overlay_page)

            pdf_writer = PdfWriter()
            pdf_writer.add_page(letterhead_page)

            with open(output_pdf, "wb") as output_file:
                pdf_writer.write(output_file)

        return output_pdf
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)

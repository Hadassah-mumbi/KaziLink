import os
from io import BytesIO
from typing import Optional
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.booking import Booking
from app.models.provider import Provider
from app.models.user import User


def generate_booking_acceptance_pdf(booking: Booking, provider: Provider, customer: User, category_name: str) -> bytes:
    """Generate a professional booking confirmation PDF using ReportLab."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin = 15 * mm
    y = height - margin

    # ============================================================
    # HEADER - Company Name and Title
    # ============================================================
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(colors.HexColor("#003366"))  # Dark blue
    c.drawString(margin, y, "KAZILINK")
    y -= 8 * mm

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#2d6b35"))  # Green accent
    c.drawString(margin, y, "Service Booking Confirmation")
    y -= 2 * mm

    # Horizontal line
    c.setStrokeColor(colors.HexColor("#2d6b35"))
    c.setLineWidth(2)
    c.line(margin, y, width - margin, y)
    y -= 5 * mm

    # ============================================================
    # BOOKING DETAILS BOX
    # ============================================================
    box_y = y - 25 * mm
    c.setFillColor(colors.HexColor("#f5f5f5"))
    c.rect(margin, box_y, width - 2*margin, 25 * mm, fill=1, stroke=1)
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.setLineWidth(0.5)

    y -= 3 * mm
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#666666"))
    
    # Booking details in columns
    col_width = (width - 2*margin) / 3
    c.drawString(margin + 2*mm, y, "BOOKING NUMBER")
    c.drawString(margin + col_width + 2*mm, y, "CONFIRMATION CODE")
    c.drawString(margin + 2*col_width + 2*mm, y, "EMAIL")
    
    y -= 5 * mm
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#003366"))
    
    booking_number = str(booking.id)[:12].upper()
    confirmation_code = str(booking.id)[-4:].upper()
    
    c.drawString(margin + 2*mm, y, booking_number)
    c.drawString(margin + col_width + 2*mm, y, confirmation_code)
    c.drawString(margin + 2*col_width + 2*mm, y, customer.email)
    
    y = box_y - 5 * mm

    # ============================================================
    # BOOKING DETAILS SECTION
    # ============================================================
    y -= 3 * mm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#003366"))
    c.drawString(margin, y, "Service Details")
    y -= 8 * mm

    # Service card with background
    card_height = 30 * mm
    c.setFillColor(colors.HexColor("#ffffff"))
    c.setStrokeColor(colors.HexColor("#2d6b35"))
    c.setLineWidth(1.5)
    c.rect(margin, y - card_height, width - 2*margin, card_height, fill=1, stroke=1)

    y -= 3 * mm
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#2d6b35"))
    c.drawString(margin + 3*mm, y, category_name)
    
    y -= 6 * mm
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#666666"))

    # Service details in grid
    detail_x = margin + 3*mm
    detail_y = y
    col_width_detail = (width - 2*margin - 6*mm) / 2

    # Left column
    c.setFont("Helvetica-Bold", 9)
    c.drawString(detail_x, detail_y, "Date:")
    c.setFont("Helvetica", 9)
    c.drawString(detail_x + 30*mm, detail_y, str(booking.booking_date))

    detail_y -= 5 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(detail_x, detail_y, "Time:")
    c.setFont("Helvetica", 9)
    c.drawString(detail_x + 30*mm, detail_y, str(booking.booking_time))

    # Right column
    detail_y = y
    right_col_x = margin + (width - 2*margin) / 2
    c.setFont("Helvetica-Bold", 9)
    c.drawString(right_col_x, detail_y, "Location:")
    c.setFont("Helvetica", 9)
    location_text = f"{booking.town}, {booking.county}"
    c.drawString(right_col_x + 30*mm, detail_y, location_text)

    detail_y -= 5 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(right_col_x, detail_y, "Status:")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#2d6b35"))
    c.drawString(right_col_x + 30*mm, detail_y, "CONFIRMED")

    y -= card_height + 5 * mm

    # ============================================================
    # PROVIDER & CUSTOMER INFORMATION
    # ============================================================
    y -= 3 * mm
    
    # Two column layout
    provider_x = margin
    customer_x = margin + (width - 2*margin) / 2 + 2*mm

    # Provider info box
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#003366"))
    c.drawString(provider_x, y, "SERVICE PROVIDER")
    y -= 6 * mm

    c.setFillColor(colors.HexColor("#f5f5f5"))
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.setLineWidth(0.5)
    c.rect(provider_x, y - 20*mm, (width - 2*margin) / 2 - 2*mm, 20*mm, fill=1, stroke=1)

    y -= 3 * mm
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#000000"))
    c.drawString(provider_x + 2*mm, y, f"{provider.user.first_name} {provider.user.last_name}")
    
    y -= 5 * mm
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawString(provider_x + 2*mm, y, f"Phone: {provider.user.phone}")
    
    y -= 4 * mm
    c.drawString(provider_x + 2*mm, y, f"Email: {provider.user.email}")

    # Customer info box
    customer_y = y + 12 * mm
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#003366"))
    c.drawString(customer_x, customer_y, "CUSTOMER")
    customer_y -= 6 * mm

    c.setFillColor(colors.HexColor("#f5f5f5"))
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.setLineWidth(0.5)
    c.rect(customer_x, customer_y - 20*mm, (width - 2*margin) / 2 - 2*mm, 20*mm, fill=1, stroke=1)

    customer_y -= 3 * mm
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#000000"))
    c.drawString(customer_x + 2*mm, customer_y, f"{customer.first_name} {customer.last_name}")
    
    customer_y -= 5 * mm
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawString(customer_x + 2*mm, customer_y, f"Phone: {customer.phone}")
    
    customer_y -= 4 * mm
    c.drawString(customer_x + 2*mm, customer_y, f"Email: {customer.email}")

    y = min(y, customer_y) - 22*mm

    # ============================================================
    # SERVICE DESCRIPTION
    # ============================================================
    if booking.description:
        y -= 3 * mm
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#003366"))
        c.drawString(margin, y, "SERVICE DESCRIPTION")
        y -= 5 * mm

        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#666666"))
        
        # Wrap text for description
        description = booking.description[:300]  # Limit to 300 chars
        if len(booking.description) > 300:
            description += "..."
        
        # Simple text wrapping
        words = description.split()
        line = ""
        line_height = 5 * mm
        for word in words:
            if c.stringWidth(line + " " + word, "Helvetica", 9) < (width - 2*margin - 4*mm):
                line += " " + word if line else word
            else:
                if line:
                    c.drawString(margin + 2*mm, y, line)
                    y -= line_height
                line = word
        if line:
            c.drawString(margin + 2*mm, y, line)

        y -= 8 * mm

    # ============================================================
    # FOOTER
    # ============================================================
    y = margin + 10 * mm
    
    c.setStrokeColor(colors.HexColor("#2d6b35"))
    c.setLineWidth(1)
    c.line(margin, y, width - margin, y)
    y -= 5 * mm

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#2d6b35"))
    c.drawString(margin, y, "✓ Booking Confirmed")
    
    y -= 5 * mm
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#666666"))
    confirmation_msg = "Your service booking has been confirmed. Please ensure both provider and customer arrive on time."
    c.drawString(margin, y, confirmation_msg)
    
    y -= 4 * mm
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(colors.HexColor("#999999"))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawString(margin, y, f"Generated by Kazilink on {timestamp}")

    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf


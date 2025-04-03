from tqdm import tqdm
from svglib.svglib import svg2rlg
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF  # Import renderPDF from reportlab.graphics
from PIL import Image


def convert_svg_to_pdf(svg_path, pdf_canvas, page_width, page_height):
    """Convert an SVG file to a PDF with a fixed page size."""
    drawing = svg2rlg(svg_path)

    # Calculate scale factors to fit the page
    scale_x = page_width / drawing.width
    scale_y = page_height / drawing.height
    scale_factor = min(scale_x, scale_y)  # Maintain aspect ratio

    # Apply scaling transformation
    drawing.scale(scale_factor, scale_factor)

    # Center the SVG on the page
    x_offset = (page_width - (drawing.width * scale_factor)) / 2
    y_offset = (page_height - (drawing.height * scale_factor)) / 2

    pdf_canvas.setPageSize((page_width, page_height))  # Set fixed page size
    renderPDF.draw(drawing, pdf_canvas, x_offset, y_offset)  # Draw SVG
    pdf_canvas.showPage()  # Move to the next page
    print(f"Converted {svg_path} to PDF page.")


def convert_png_to_pdf(png_path, pdf_canvas, page_width, page_height):
    """Convert a PNG file to a PDF with a fixed page size."""
    image = Image.open(png_path)
    width, height = image.size
    # Scale the image to fit the page size
    scale_x = page_width / width
    scale_y = page_height / height
    scale_factor = min(scale_x, scale_y)  # Maintain aspect ratio

    # Adjust image size to fit the page
    width *= scale_factor
    height *= scale_factor

    pdf_canvas.setPageSize((page_width, page_height))  # Use fixed page size
    pdf_canvas.drawImage(
        png_path, 0, 0, width=width, height=height
    )  # Draw the scaled PNG
    pdf_canvas.showPage()  # Move to the next page
    print(f"Converted {png_path} to PDF page.")


def create_pdf_from_images(
    image_paths, output_pdf_path, page_width=A4[0], page_height=A4[1]
):
    """Create a PDF where each image (SVG/PNG) is on a separate page with the same size."""
    pdf_canvas = canvas.Canvas(output_pdf_path)

    for image_path in tqdm(image_paths):
        if image_path.endswith(".svg"):
            convert_svg_to_pdf(image_path, pdf_canvas, page_width, page_height)
        elif image_path.endswith(".png"):
            convert_png_to_pdf(image_path, pdf_canvas, page_width, page_height)
        else:
            print(f"Unsupported file format: {image_path}")

    pdf_canvas.save()  # Finalize and save the PDF
    print(f"PDF created successfully: {output_pdf_path}")


if __name__ == "__main__":
    image_files = [
        "scores_parts/894f922d14092db4b26bafc1b013387c321f45a8/0_894f922d14092db4b26bafc1b013387c321f45a8.svg",
        "scores_parts/894f922d14092db4b26bafc1b013387c321f45a8/1_894f922d14092db4b26bafc1b013387c321f45a8.svg",
    ]
    output_pdf = "output.pdf"
    page_width, page_height = A4

    create_pdf_from_images(image_files, output_pdf, page_width, page_height)

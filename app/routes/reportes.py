from flask import Blueprint, send_file
from flask_login import login_required
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
from app.services.producto_service import get_all as get_productos
from app.services.cliente_service import get_all as get_clientes

bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@bp.route('/productos')
@login_required
def productos_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Listado de Productos", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    productos = get_productos()
    data = [['ID', 'Nombre', 'Precio', 'Stock']]
    for p in productos:
        data.append([str(p.id), p.nombre, f"${p.precio:.2f}", str(p.stock)])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='productos.pdf', mimetype='application/pdf')

@bp.route('/clientes')
@login_required
def clientes_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Listado de Clientes", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    clientes = get_clientes()
    data = [['ID', 'Nombre', 'Cédula', 'Email', 'Teléfono']]
    for c in clientes:
        data.append([str(c.id), c.nombre, c.cedula or '-', c.email or '-', c.telefono or '-'])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='clientes.pdf', mimetype='application/pdf')

@bp.route('/usuarios')
@login_required
def usuarios_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Listado de Usuarios", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    from app.services.usuario_service import get_all as get_usuarios
    usuarios = get_usuarios()
    data = [['ID', 'Nombre', 'Email', 'Teléfono', 'Rol']]
    for u in usuarios:
        data.append([str(u.id), u.nombre, u.mail, u.telefono or '-', u.rol])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='usuarios.pdf', mimetype='application/pdf')
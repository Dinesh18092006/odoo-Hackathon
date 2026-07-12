"""
Asset tag and QR code generator utilities.
Asset Tag format: AST-YYYY-XXXXXX (e.g., AST-2025-000042)
"""
import io
import os
import qrcode
from datetime import datetime
from qrcode.image.pure import PyPNGImage
from config import settings


def generate_asset_tag(sequence_number: int) -> str:
    """
    Generate a unique asset tag in format: AST-YYYY-XXXXXX
    Args:
        sequence_number: Auto-incremented sequence (stored in DB)
    Returns:
        str: Asset tag like 'AST-2025-000042'
    """
    year = datetime.now().year
    return f"AST-{year}-{sequence_number:06d}"


def generate_qr_code(asset_tag: str, asset_id: str) -> str:
    """
    Generate a QR code PNG for an asset and save it to disk.
    Args:
        asset_tag: The asset tag (e.g. AST-2025-000042)
        asset_id: UUID of the asset
    Returns:
        str: Relative URL path to the saved QR code PNG
    """
    qr_dir = os.path.join(settings.upload_dir, "qrcodes")
    os.makedirs(qr_dir, exist_ok=True)

    # QR code encodes a URL that could link to the asset detail page
    qr_data = f"ASSETFLOW:ASSET:{asset_id}:{asset_tag}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    file_name = f"qr_{asset_id}.png"
    file_path = os.path.join(qr_dir, file_name)
    img.save(file_path)

    return f"/uploads/qrcodes/{file_name}"

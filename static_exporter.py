from __future__ import annotations

from pathlib import Path
import json
import shutil
from urllib.parse import quote


def path_to_output_file(output_dir: Path, route_path: str) -> Path:
    normalized = route_path.lstrip('/')
    if not normalized:
        return output_dir / 'index.html'
    if normalized.endswith('.html'):
        return output_dir / normalized
    return output_dir / normalized / 'index.html'


def serialize_certificate(certificate):
    submission = next(
        (
            item
            for item in certificate.user.submissions
            if item.product_id == certificate.product_id
        ),
        None,
    )
    return {
        'cert_code': certificate.cert_code,
        'issued_to': certificate.user.name or 'Certificate Holder',
        'program': certificate.product.title,
        'category': certificate.product.category,
        'issue_date': certificate.created_at.strftime('%Y-%m-%d'),
        'status': 'Successfully Completed and Verified.',
        'github_link': submission.github_link if submission else '',
    }


def export_static_site(flask_app, product_model, certificate_model, get_domain_names):
    output_dir = Path(flask_app.root_path) / 'docs'
    static_dir = Path(flask_app.root_path) / 'static'
    data_dir = output_dir / 'data'

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / '.nojekyll').write_text('', encoding='utf-8')

    if static_dir.exists():
        shutil.copytree(static_dir, output_dir / 'static', dirs_exist_ok=True)

    with flask_app.app_context():
        products = product_model.query.order_by(product_model.id.asc()).all()
        domains = get_domain_names()
        certificates = certificate_model.query.order_by(certificate_model.id.asc()).all()

        routes = [
            '/',
            '/verification',
        ]
        routes.extend(f'/details/{product.id}' for product in products)
        routes.extend(f'/domain/{quote(domain, safe="")}' for domain in domains)
        routes.extend(f'/certificate/{quote(certificate.cert_code, safe="")}' for certificate in certificates)

        flask_app.config['STATIC_EXPORT_MODE'] = True
        client = flask_app.test_client()

        try:
            for route_path in routes:
                response = client.get(route_path)
                if response.status_code != 200:
                    raise RuntimeError(
                        f'Static export failed for {route_path} with status {response.status_code}.'
                    )

                output_file = path_to_output_file(output_dir, route_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(response.get_data(as_text=True), encoding='utf-8')

            data_dir.mkdir(parents=True, exist_ok=True)
            certificates_file = data_dir / 'certificates.json'
            certificates_file.write_text(
                json.dumps(
                    [serialize_certificate(certificate) for certificate in certificates],
                    indent=2,
                ),
                encoding='utf-8',
            )
        finally:
            flask_app.config['STATIC_EXPORT_MODE'] = False

    return output_dir

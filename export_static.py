from app import app, Certificate, Product, get_all_domain_names
from static_exporter import export_static_site


if __name__ == '__main__':
    output_dir = export_static_site(
        app,
        Product,
        Certificate,
        get_all_domain_names,
    )
    print(f'Static site exported to {output_dir}')

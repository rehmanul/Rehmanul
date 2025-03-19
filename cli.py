#!/usr/bin/env python3
import click
import os
from extraction_service import extraction_service
from logging_system import setup_logging

# Set up logging
logger = setup_logging()

@click.group()
def cli():
    """Web Stryker R7 - Advanced Web Data Extraction Tool"""
    pass

@cli.command()
@click.argument('url')
@click.option('--output', '-o', help='Output file path', default='results.json')
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), default='json')
def extract(url, output, format):
    """Extract data from a single URL"""
    try:
        result = extraction_service.process_url(url, "cli-single")
        click.echo(f"Extraction successful: {result}")
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.argument('file_path')
@click.option('--concurrent', '-c', help='Number of concurrent extractions', default=5)
@click.option('--output-dir', '-o', help='Output directory', default='results')
def batch(file_path, concurrent, output_dir):
    """Process multiple URLs from a file"""
    try:
        with open(file_path) as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for url in urls:
            try:
                result = extraction_service.process_url(url, "cli-batch")
                output_file = os.path.join(output_dir, f"{hash(url)}.json")
                with open(output_file, 'w') as f:
                    f.write(str(result))
                click.echo(f"Processed {url} -> {output_file}")
            except Exception as e:
                logger.error(f"Failed to process {url}: {str(e)}")
                click.echo(f"Error processing {url}: {str(e)}", err=True)
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
def version():
    """Show version information"""
    click.echo("Web Stryker R7 Python Edition v1.0.0")

if __name__ == '__main__':
    cli()

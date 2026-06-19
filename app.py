#!/usr/bin/env python3
# Copyright (c) 2021, Anders Lervik.
# Distributed under the LGPLv2.1+ License. See LICENSE for more info.
"""
Flask web server for gpxplotter.

This module provides a simple REST API for accessing GPX route information.
"""
import os
import pathlib
from flask import Flask, jsonify, request
from gpxplotter import read_gpx_file

app = Flask(__name__)

# Configure the directory where GPX files are stored
# This can be overridden by setting the GPX_DATA_DIR environment variable
GPX_DATA_DIR = os.environ.get('GPX_DATA_DIR', './examples/jupyter')


def get_gpx_files():
    """Get all GPX files from the configured directory."""
    data_dir = pathlib.Path(GPX_DATA_DIR)
    if not data_dir.exists():
        return []
    return list(data_dir.glob('*.gpx'))


@app.route('/api/routes', methods=['GET'])
def get_routes():
    """
    GET endpoint that returns a list of route names from all GPX files.
    
    Returns
    -------
    json
        A JSON object containing:
        - routes: list of route information dictionaries
        - count: total number of routes found
        
    Each route dictionary contains:
        - name: the route name (from GPX file)
        - type: the route type (if available)
        - file: the source GPX filename
    """
    try:
        gpx_files = get_gpx_files()
        
        if not gpx_files:
            return jsonify({
                'routes': [],
                'count': 0,
                'message': f'No GPX files found in {GPX_DATA_DIR}'
            }), 200
        
        routes = []
        for gpx_file in gpx_files:
            try:
                for track in read_gpx_file(str(gpx_file)):
                    route_info = {
                        'name': track.get('name', ['Unknown'])[0] if track.get('name') else 'Unknown',
                        'type': track.get('type', [''])[0] if track.get('type') else '',
                        'file': gpx_file.name
                    }
                    routes.append(route_info)
            except Exception as e:
                app.logger.error(f'Error reading {gpx_file.name}: {str(e)}')
                continue
        
        return jsonify({
            'routes': routes,
            'count': len(routes)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to retrieve routes'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'gpx_data_dir': GPX_DATA_DIR,
        'gpx_files_found': len(get_gpx_files())
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information."""
    return jsonify({
        'name': 'gpxplotter API',
        'version': '1.0.0',
        'endpoints': {
            '/': 'This information page',
            '/api/health': 'Health check endpoint',
            '/api/routes': 'GET list of all route names'
        }
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

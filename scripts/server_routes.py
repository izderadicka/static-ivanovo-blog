"""Server adapter for old WordPress query URLs and extensionless RSS routes."""
import json


def nginx_files(articles):
    entries = '\n'.join('    ' + a['id'] + ' ' + json.dumps(a['path']) + ';' for a in articles if a['ready'])
    maps = ('# Include inside nginx http {}, before the server block.\n'
            'map $arg_p $wp_post_path {\n    default "";\n' + entries + '\n}\n'
            'map $arg_page_id $wp_page_path {\n    default "";\n' + entries + '\n}\n'
            'map $args $wp_remaining_args {\n    default $args;\n'
            '    ~^(?:p|page_id)=[^&]*&?(.*)$ $1;\n'
            '    ~^(.*)&(?:p|page_id)=[^&]*(&.*)?$ $1$2;\n}\n'
            'map $wp_remaining_args $wp_query {\n    default "?$wp_remaining_args";\n    "" "";\n}\n')
    server = '''# Example only: integrate the maps at http scope and adapt root/TLS/proxy.
server {
    listen 80;
    server_name zderadicka.eu;
    root /site/current;
    index index.html;
    error_page 404 /404.html;
    location = / {
        if ($wp_post_path != "") { return 308 $wp_post_path$wp_query; }
        if ($wp_page_path != "") { return 308 $wp_page_path$wp_query; }
        if ($arg_p != "") { return 404; }
        if ($arg_page_id != "") { return 404; }
        if ($arg_s != "") { return 302 /search/?q=$arg_s; }
        try_files /index.html =404;
    }
    location ~ /feed/?$ {
        types { }
        default_type application/rss+xml;
        add_header X-Robots-Tag "noindex";
        try_files $uri/index.html =404;
    }
    location ~ ^(.*/feed/)rss2/?$ { return 308 $1; }
    location / { try_files $uri $uri/ =404; }
}
'''
    return {'redirects/nginx-maps.conf': maps.encode(), 'redirects/nginx-site.conf': server.encode()}

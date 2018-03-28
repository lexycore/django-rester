import os
import json
import yaml

from django_rester.singleton import Singleton
from django_rester.swagger.url_map import UrlMap
from django_rester.swagger.settings import rester_swagger_settings


class SwaggerGenerator(metaclass=Singleton):
    swagger_version = '2.0'
    make_swagger_file = rester_swagger_settings['GENERATE_SWAGGER_FILE']
    swagger_info = rester_swagger_settings['INFO']
    type_str_map = {str: "string", int: "integer", float: "number", bool: "boolean"}

    def __init__(self, url_map=None):
        self.url_map = url_map or UrlMap()
        self.path_parameter = 'query'
        self.swagger_data = [{"swagger": "2.0"}, {"info": self.swagger_info}, {"paths": self.generate_paths()}]
        if self.make_swagger_file:
            pass

    @staticmethod
    def check_json_data(data):
        return json.loads(json.dumps(data))

    def generate_paths(self):
        paths = {}
        for url, view in self.url_map.items():
            path = {url: self.generate_data_for_view(view)}
            paths.update(path)

        return paths


    def generate_data_for_view(self, view):
        base_structure, parameters = {}, []
        if isinstance(view.swagger_fields, dict) and isinstance(view.request_fields, dict):
            for method, swagger_fields in view.swagger_fields.items():
                base_structure = {method: {k: v for k, v in swagger_fields.__dict__.items()}}

            for method, request_structure in view.request_fields.items():
                method_dict = base_structure.get(method)

                if method_dict:
                    for field_name, field_value in request_structure.items():
                        parameter = {
                            "in": self.path_parameter, "name": field_name,
                            "required": field_value.required, "type": self.type_str_map.get(field_value.field_type),
                            "description": field_value.description
                        }
                        if not field_value.required:
                            parameter.update({"default": field_value.default})
                        parameters.append(parameter)
                    method_dict.update({'parameters': parameters})
        return base_structure

    def generate_file(self):
        for swagger_item in self.swagger_data:
            with open('swagger.yaml', 'a') as f:
                yaml.dump(swagger_item, f, default_flow_style=False)
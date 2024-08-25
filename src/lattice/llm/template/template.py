import os
from jinja2 import Environment, FileSystemLoader

def find_template_files(directory):
    """
    Recursively scans the given directory for files ending with `.tmpl`
    and returns a dictionary mapping the relative file path to the file name without the `.tmpl` extension.

    :param directory: The root directory to start scanning.
    :return: A dictionary with the relative file path as the key and the template file name without `.tmpl` as the value.
    """
    template_files = {}

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.tmpl'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                template_name = file[:-5]  # Remove the .tmpl extension
                template_files[relative_path] = template_name

    return template_files

class TemplateEngine:
    def __init__(self, template_dir):
        """
        Initialize the template engine with the directory to scan for templates.

        :param template_dir: The root directory where templates are located.
        """
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.templates = find_template_files(template_dir)

    def render_template(self, template_name, context):
        """
        Renders the template with the given context.

        :param template_name: The name of the template to render (without .tmpl).
        :param context: A dictionary containing the context to pass to the template.
        :return: The rendered content as a string.
        """
        template_path = None
        for path, name in self.templates.items():
            if name == template_name:
                template_path = path
                break
        
        if template_path is None:
            raise FileNotFoundError(f"Template '{template_name}' not found in directory '{self.template_dir}'.")

        template = self.env.get_template(template_path)
        return template.render(context)

if __name__ == "__main__":
    # Example usage
    template_directory = "/path/to/your/directory"
    engine = TemplateEngine(template_directory)

    context = {
        'title': 'Hello, World!',
        'body': 'This is a rendered template using Jinja2.'
    }

    rendered_content = engine.render_template('example_template', context)
    print(rendered_content)

from dress_blog.models import Config

def config(request):
    """
    Adds configuration information to the context.

    To employ, add the conf method reference to your project
    settings TEMPLATE_CONTEXT_PROCESSORS.

    Example:
        TEMPLATE_CONTEXT_PROCESSORS = (
            ...
            "dress_blog.context_processors.config",
        )
    """
    return {'dress_blog_config': Config.get_current()}

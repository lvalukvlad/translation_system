from flask import Blueprint, request, render_template, flash
from app.controllers.translation_controller import TranslationController
from app.models.context import Context
import os

translation_bp = Blueprint('translation', __name__)
trans_controller = TranslationController()


@translation_bp.route('/translate', methods=['GET', 'POST'])
def translate():
    result = None
    if request.method == 'POST':
        content = request.form['content']
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and file.filename.endswith('.txt'):
                content = file.read().decode('utf-8')

        source_lang = request.form['source_lang']
        target_lang = request.form['target_lang']
        dialect = request.form.get('dialect', '')
        domain = request.form.get('domain', '')
        style = request.form.get('style', 'neutral')
        audience = request.form.get('audience', '')

        context = Context(domain=domain, style=style, audience=audience)

        text_id = trans_controller.process_text(content, source_lang, context.__dict__)
        trans_id, draft = trans_controller.generate_draft(text_id, target_lang, dialect)

        trans_controller.translations.append({
            'trans_id': trans_id,
            'text_id': text_id,
            'content': content,
            'draft': draft,
            'final_version': '',
            'status': 'draft'
        })
        from app.services.storage_service import StorageService
        StorageService.save_json('translations.json', trans_controller.translations)

        result = draft

    return render_template('translate.html', result=result)
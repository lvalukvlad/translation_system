from flask import Blueprint, request, render_template, flash, redirect, url_for
from app.controllers.translation_controller import TranslationController
from app.models.context import Context
import os

translation_bp = Blueprint('translation', __name__)
trans_controller = TranslationController()


@translation_bp.route('/translate', methods=['GET', 'POST'])
def translate():
    result = None
    if request.method == 'POST':
        content = request.form.get('content', '').strip()

        # Если файл загружен → читаем его
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and file.filename.endswith('.txt'):
                content = file.read().decode('utf-8').strip()

        # Проверяем, что есть текст
        if not content:
            flash("Введите текст или загрузите файл.")
            return render_template('translate.html', result=result)

        source_lang = request.form['source_lang']
        target_lang = request.form['target_lang']
        dialect = request.form.get('dialect', '')
        domain = request.form.get('domain', '')
        style = request.form.get('style', 'neutral')
        audience = request.form.get('audience', '')

        context = Context(domain=domain, style=style, audience=audience)

        text_id = trans_controller.process_text(content, source_lang, context.__dict__)
        trans_id, draft = trans_controller.generate_draft(text_id, target_lang, dialect)

        # Сохраняем перевод
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

        result = draft  # ← Сохраняем результат

    return render_template('translate.html', result=result)


@translation_bp.route('/edit-draft/<trans_id>', methods=['GET', 'POST'])
def edit_draft(trans_id):
    # Найдём перевод
    trans = next((t for t in trans_controller.translations if t['trans_id'] == trans_id), None)
    if not trans:
        flash('Перевод не найден')
        return redirect(url_for('translation.dashboard'))

    if request.method == 'POST':
        # Обновим черновик
        new_draft = request.form['draft']
        trans['draft'] = new_draft
        from app.services.storage_service import StorageService
        StorageService.save_json('translations.json', trans_controller.translations)
        flash('Черновик обновлён')
        return redirect(url_for('translation.dashboard'))

    return render_template('edit_draft.html', translation=trans)


@translation_bp.route('/dashboard')
def dashboard():
    # Загрузим переводы
    from app.services.storage_service import StorageService
    translations = StorageService.load_json('translations.json', [])
    return render_template('dashboard.html', translations=translations)

@translation_bp.route('/graph')
def view_graph():
    from app.services.storage_service import StorageService
    graph = StorageService.load_json('knowledge_graph.json', {})
    return render_template('graph.html', graph=graph)
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('translate-form');
  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();

      const content = document.getElementById('content').value;
      const source_lang = document.getElementById('source_lang').value;
      const target_lang = document.getElementById('target_lang').value;
      const style = document.getElementById('style').value;
      const dialect = document.getElementById('dialect').value;

      const response = await fetch('/api/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          context: { style },
          dialect
        })
      });

      const data = await response.json();
      if (data.message) {
        document.getElementById('result').innerHTML = `<h3>Результат перевода:</h3><p><strong>${data.message}</strong></p>`;
      } else {
        document.getElementById('result').innerHTML = `<h3>Результат перевода:</h3><p><strong>${data.draft}</strong></p>`;
      }
      document.getElementById('result').style.display = 'block';
    };
  }

  const buttons = document.querySelectorAll('button');
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      button.innerHTML = 'Обработка...';
      setTimeout(() => {
        button.innerHTML = 'Перевести';
      }, 1500);
    });
  });
});
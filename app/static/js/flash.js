function flash(msg, type='info') {
    const flashBox = document.getElementById('flashes');
    if (!flashBox)
        return;
    const el = document.createElement('div');
    el.className = `flash ${type}`;
    el.innerHTML = `
        <span class="content">${msg}</span>
        <span class="flash-close">
            <span class="material-icons icon">close</span>
        </span>
    `;

    flashBox.appendChild(el);
    setupFlashClose(el);
}

function setupFlashClose(el) {
    const close = el.querySelector('.flash-close');
    if (!close)
        return;
    close.addEventListener('click', () => el.remove());
}

onLoad(() => {
    for (const el of document.querySelectorAll('.flash')) {
        setupFlashClose(el);
    }
});

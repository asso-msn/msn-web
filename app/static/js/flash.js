for (const el of document.querySelectorAll('.flash')) {
    const close = el.querySelector('.flash-close');

    if (!close)
        continue;

    close.addEventListener('click', () => el.remove());
}

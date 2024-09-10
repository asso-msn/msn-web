
onLoad(() => {
    const showMore = document.querySelector('.user-games .show-more');
    const games = document.querySelector('.user-games');

    if (showMore && games) {
        const expand = showMore.querySelector('[data-action="expand"]');
        const shrink = showMore.querySelector('[data-action="shrink"]');


        if (expand && shrink) {
            expand.addEventListener('click', () => {
                games.classList.remove('limited');
                expand.classList.add('hidden');
                shrink.classList.remove('hidden');
            });

            shrink.addEventListener('click', () => {
                games.classList.add('limited');
                expand.classList.remove('hidden');
                shrink.classList.add('hidden');
            });
        }
    }
});

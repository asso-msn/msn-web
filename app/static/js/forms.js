for (const el of document.querySelectorAll(".input .password")) {
    const show = el.querySelector(".show");
    const hide = el.querySelector(".hide");
    const input = el.querySelector("input");

    if (!show || !hide || !input)
        continue;

    el.classList.add("hide");

    show.addEventListener("click", () => {
        el.classList.remove("hide");
        el.classList.add("show");
        input.type = "text";
    });
    hide.addEventListener("click", () => {
        el.classList.remove("show");
        el.classList.add("hide");
        input.type = "password";
    });

    console.log(`registed ${el}`);
}

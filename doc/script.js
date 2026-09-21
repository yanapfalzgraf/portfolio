const STREAMLIT_URL =
    "https://portfolio-katkadfbffcvskia9pwhdm.streamlit.app/";

let isLeaving = false;


/*
------------------------------------------------
TRY TO CONTACT STREAMLIT EARLY
------------------------------------------------

This is only a best-effort request.

Whether Streamlit Community Cloud actually wakes
the sleeping app from this request can vary.

The portfolio link works independently of this.
*/

function warmUpStreamlit() {

    fetch(STREAMLIT_URL, {
        mode: "no-cors",
        cache: "no-store"
    }).catch(() => {
        // Intentionally ignored.
        // The landing page must continue working.
    });

}


/*
------------------------------------------------
OPEN PORTFOLIO
------------------------------------------------
*/

function openPortfolio() {

    if (isLeaving) {
        return;
    }

    isLeaving = true;

    const transition =
        document.querySelector(".transition-screen");

    transition.classList.add("visible");


    /*
        Short transition so the navigation does
        not feel like an abrupt external redirect.
    */

    setTimeout(() => {

        window.location.href = STREAMLIT_URL;

    }, 450);

}


/*
------------------------------------------------
BUTTONS
------------------------------------------------
*/

document
    .querySelectorAll(".js-portfolio-link")
    .forEach(element => {

        element.addEventListener("click", event => {

            event.preventDefault();

            openPortfolio();

        });

    });


/*
------------------------------------------------
SCROLL DOWN AT BOTTOM
------------------------------------------------

Only redirect when the visitor is already near
the bottom and deliberately scrolls further down.

This avoids redirecting on every normal scroll.
*/

window.addEventListener(
    "wheel",
    event => {

        if (event.deltaY <= 0 || isLeaving) {
            return;
        }

        const viewportBottom =
            window.scrollY + window.innerHeight;

        const documentHeight =
            document.documentElement.scrollHeight;

        const nearBottom =
            viewportBottom >= documentHeight - 40;

        if (nearBottom) {
            openPortfolio();
        }

    },
    { passive: true }
);


/*
------------------------------------------------
START
------------------------------------------------
*/

window.addEventListener("load", () => {

    /*
        Give the landing page priority and then
        contact Streamlit shortly afterwards.
    */

    setTimeout(warmUpStreamlit, 500);

});
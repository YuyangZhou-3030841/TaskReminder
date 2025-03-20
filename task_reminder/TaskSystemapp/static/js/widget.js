/**
 * Click on the widget area to return to the home page
 */
function returnToHomepage() {
    if (window.opener && !window.opener.closed) {
        window.opener.close();
        window.open(window.location.origin + window.location.pathname, '_blank');
    } else {
        window.open(window.location.origin + window.location.pathname, '_blank');
    }
    window.close();
}

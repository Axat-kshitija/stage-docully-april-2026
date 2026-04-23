// cdr custom js


$(document).ready(function() {
    $('#userProfileCdr').on('show.bs.modal', function() {
        setTimeout(function() {
            $('.modal-backdrop').addClass('md-white');
        }, 10);
    });

    $('#userProfileCdr').on('hidden.bs.modal', function() {
        $('.modal-backdrop').removeClass('md-white');
    });
})
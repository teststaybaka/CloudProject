$(document).ready(function() {
    $('.change-settings-form').submit(function(evt) {
        evt.preventDefault();
        $.ajax({
            type: 'POST',
            data: $(this).serialize(),
            success: function(result) {
                if (result.error) {
                    console.log(result.message);
                } else {
                    window.location.replace('/');
                }
            }
        })
    });
});
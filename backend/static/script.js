$(document).ready(function() {
    // $("#post-button").click(function() {
    //     const url = "http://localhost:5000/post";
    //     const postInfo = {
    //         title: $("#title").val(),
    //         description: $("#description").val()
    //     };
    // });
    // $.ajax({
    //     url: url,
    //     type: "POST",
    //     data: JSON.stringify(postInfo),
    //     processData: false,
    //     contentType: "application/json; charset=UTF-8",
    //     complete: function() {
    //         console.log("request complete!");
    //         window.location.reload();
    //     }
    // });
    $("#sidebar").mCustomScrollbar({
        theme: "minimal"
    });
   
    $('#sidebarCollapse').on('click', function () {
        // open or close navbar
        $('#sidebar').toggleClass('active');
        // close dropdowns
        $('.collapse.in').toggleClass('in');
        // and also adjust aria-expanded attributes we use for the open/closed arrows
        // in our CSS
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });

});
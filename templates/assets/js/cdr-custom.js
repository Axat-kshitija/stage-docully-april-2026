// cdr custom js
// declare var $: any;

$(document).ready(function() {
    $('#userProfileCdr').on('show.bs.modal', function() {
        setTimeout(function() {
            $('.modal-backdrop').addClass('md-white');
        }, 10);
    });

    $('#userProfileCdr').on('hidden.bs.modal', function() {
        $('.modal-backdrop').removeClass('md-white');
	});
	
	alert('body');

    // page height
 //    function footerAlign() {
	//   $('footer').css('display', 'block');
	//   $('footer').css('height', 'auto');
	//   var footerHeight = $('footer').outerHeight();
	//   $('body').css('padding-bottom', footerHeight);
	//   $('footer').css('height', footerHeight);
	// }


	// $(document).ready(function(){
	//   footerAlign();
	// });

	// $( window ).resize(function() {
	//   footerAlign();
	// });
	

 //    var div = $(".addclass").height();
	// var win = $(window).height();

	// if (div < win ) {
	//     $("footer").addClass('fixed');
	// }
})
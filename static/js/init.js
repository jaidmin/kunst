(function($){
  $(function(){

      $('.button-collapse').sideNav();
      $('.parallax').parallax();
      $('ul.tabs').tabs();
      $('.materialboxed').materialbox();
      $('.carousel').carousel();
      $('.slider').slider();
      $('select').material_select();
      $("form").submit(function() {
    $("input").removeAttr("disabled");

});


  }); // end of document ready


})(jQuery); // end of jQuery name space
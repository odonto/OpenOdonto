angular.module('opal.controllers').controller(
  'CheckFP17OStep',
  function(
    scope,
    step,
    episode,
    $timeout,
    $rootScope,
    FormValidation,
    DateOfBirthRequired
){
  "use strict";
  $rootScope.isFormValid = null;
  $rootScope.showSummary = null;
  var validators = [
    DateOfBirthRequired,
    AddressRequired
  ];

  var validate = function(){
    if(scope.form.$valid){
      var errors = FormValidation(scope.editing, validators);
      $rootScope.isFormValid = !_.size(errors);
      $rootScope.errors = errors;
    }
    else{
      $rootScope.isFormValid = false;
    }
  }

  scope.$watch("editing", validate, true);

  $timeout(function(){
    scope.form.$setSubmitted();
    validate();
    $rootScope.showSummary = $rootScope.isFormValid;
  });
});


angular.module('opal.services').factory('Fp17Under18', function(toMomentFilter){

  /*
  * An FP17 can have multiple dates so look at them all starting with the earliest
  * and make sure the patient was under 20 at the time (let's give some leeway)
  */
  return function(editing){
    if(!editing.fp17_exemptions.patient_under_18){
      return;
    }
    if(editing.demographics.date_of_birth){
      var otherDate = editing.fp17_incomplete_treatment.date_of_acceptance;
      otherDate = otherDate || editing.fp17_incomplete_treatment.completion_or_last_visit;

      if(otherDate){
        var otherMoment = toMomentFilter(otherDate);

        var dobMoment = toMomentFilter(editing.demographics.date_of_birth);
        var diff = otherMoment.diff(dobMoment, "years", false);
        if(diff > 20){
          return {
            fp17_exemptions: {
              patient_under_18: "The patient's DOB was over 18 years ago"
            }
          }
        }
      }
    }
  }
});

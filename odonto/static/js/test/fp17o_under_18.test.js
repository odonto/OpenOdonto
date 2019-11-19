describe('Fp17oUnder18', function() {
  "use strict";
  var Fp17oUnder18;
  var editing;

  beforeEach(module('opal.filters'));
  beforeEach(module('opal.services'));

  beforeEach(function(){
      inject(function($injector){
        Fp17oUnder18  = $injector.get('Fp17oUnder18');
      });
      editing = {
        demographics: {},
        fp17_exemptions: {},
        orthodontic_assessment: {},
        orthodontic_treatment: {}
      };
  });


  describe('if a patient has the under 18 exemption it should error if their dob is older', function(){
    it('should return an error message if dob is to recent', function(){
      editing.demographics.date_of_birth = new Date(1980, 1, 1);
      editing.orthodontic_assessment.date_of_referral = new Date(2019, 1, 1);
      editing.fp17_exemptions.patient_under_18 = true;
      var expected = {
        fp17_exemptions: {
          patient_under_18: "The patient's DOB was over 18 years ago"
        }
      }
      expect(Fp17oUnder18(editing)).toEqual(expected);
    });

    it('should not error if the exemption is not clicked', function(){
      editing.demographics.date_of_birth = new Date(1980, 1, 1);
      editing.orthodontic_assessment.date_of_referral = new Date(2019, 1, 1);
      editing.fp17_exemptions.patient_under_18 = false;
      expect(Fp17oUnder18(editing)).toBe(undefined);
    });

    it('should not error if the date of birth is under 18 years ago', function(){
      editing.demographics.date_of_birth = new Date(2015, 1, 1);
      editing.orthodontic_assessment.date_of_referral = new Date(2019, 1, 1);
      editing.fp17_exemptions.patient_under_18 = true;
      expect(Fp17oUnder18(editing)).toBe(undefined);
    });

    it('should prioritise the date of referral', function(){
      editing.demographics.date_of_birth = new Date(2003, 1, 1);
      editing.orthodontic_assessment.date_of_referral = new Date(2018, 1, 1);
      editing.orthodontic_assessment.date_of_assessment = new Date(2033, 1, 1);
      editing.fp17_exemptions.patient_under_18 = true;
      expect(Fp17oUnder18(editing)).toBe(undefined);
    });
  });
});
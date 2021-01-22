function(prefix) {
   local databases = [
    'assets_maintenance'
    'book_2'
    'company_1'
    'course_teach'
    'decoration_competition'
    'election_representative'
    'match_season'
    'perpetrator'
    'station_weather'
    'wedding'
    'activity_1'
    'body_builder'
    'candidate_poll'
    'city_record'
    'college_1'
    'cre_Doc_Control_Systems'
    'cre_Drama_Workshop_Groups'
    'customers_and_invoices'
    'customers_and_products_contacts'
    'department_management'
    'driving_school'
    'employee_hire_evaluation'
    'flight_2'
    'game_injury'
    'imdb'
    'insurance_and_eClaims'
    'local_govt_in_alabama'
    'machine_repair'
    'mountain_photos'
    'music_2'
    'products_for_hire'
    'restaurant_1'
    'sakila_1'
    'school_bus'
    'school_player'
    'soccer_1'
    'store_product'
    'storm_record'
    'student_1'
    'student_assessment'
    'workshop_paper'
    'yelp'
  ]
  name: 'text2sqlvi',
 paths: [
  prefix + 'database/%s/examples.json' % [db]
  for db in databases
 ],
 tables_paths: [
  prefix + 'database/%s/tables.json' % [db]
  for db in databases
 ],
 db_path: prefix + 'database'
}

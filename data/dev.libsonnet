function(prefix) {
   local databases = [
    'architecture',
    'cinema',
    'college_3',
    'concert_singer',
    'customers_campaigns_ecommerce',
    'customers_card_transactions',
    'document_management',
    'e_learning',
    'farm',
    'flight_company',
    'manufacturer',
    'museum_visit',
    'network_1',
    'party_host',
    'phone_market',
    'product_catalog',
    'scientist_1',
    'ship_mission',
    'singer',
    'sports_competition',
    'swimming',
    'tracking_share_transactions',
    'train_station',
    'voter_1',
    'wta_1'
  ],
  name: 'text2sqlvi',
 paths: [
  prefix + 'database/%s/examples.json' % [db]
  for db in databases
 ],
 tables_paths: [
  prefix + 'database/%s/tables.json' % [db]
  for db in databases
 ],
 db_path: prefix + 'database',
}

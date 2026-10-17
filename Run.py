from Scripts import Mytek, ScoopGaming, Tunisianet, build_db



# This script is used to scrape all the necessary data and store it in the database for the application.
Tunisianet.main()
Mytek.main()
ScoopGaming.main()
build_db.main()

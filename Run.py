from Main.Code.Scripts import DB, Mytek, ScoopGaming, Tunisianet, ProductMatching
import runpy



# This script is used to scrape all the necessary data and store it in the database for the application.
Tunisianet.main()
Mytek.main()
ScoopGaming.main()
DB.main()
ProductMatching.main()
runpy.run_path("Main/Code/App/app.py", run_name = "__main__")
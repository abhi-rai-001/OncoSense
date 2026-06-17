Step 1: Push to GitHub
If your project isn't on GitHub yet, you need to push it there. Render connects directly to your GitHub repository to build the application.

Step 2: Create a Render Account
Go to Render.com and sign up (using your GitHub account makes it easiest).
Once logged in, click the "New +" button in the top right corner.
Select "Web Service".
Step 3: Connect Your Repository
Select "Build and deploy from a Git repository".
Connect your GitHub account if prompted, and select the repository containing this Final Year Project.
Click Connect.
Step 4: Configure the Web Service
You will be taken to a configuration page. Fill it out exactly like this:

Name: Give it a name (e.g., oncosense-cadrres or whatever your project name is).
Region: Pick whichever is closest to you or your users.
Branch: main (or master, whichever you use).
Runtime: Select Docker (This is crucial! It tells Render to look for your Dockerfile).
Step 5: Add Environment Variables (Important!)
Scroll down to the Environment Variables section and click "Add Environment Variable":

Key: GEMINI_API_KEY
Value: Paste your actual Gemini API Key here (Render keeps this secret and injects it into the container when it runs).
Step 6: Deploy
Scroll down to the bottom, make sure the Free Tier is selected, and click Create Web Service.
You will see a terminal log screen. Render will now pull your repository, build the Docker container (which takes 2-3 minutes), and launch it.
Once the logs say “Your service is live 🎉”, you can click the URL at the top left of the screen (it will look something like your-project.onrender.com).
That's it! Every time you push a new change to GitHub, Render will automatically detect it, rebuild the Docker container, and deploy the new version without any downtime.


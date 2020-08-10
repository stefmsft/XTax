docker build -t xcorp/xtax:latest .
docker kill xtax 2> nul
docker rm xtax 2> nul
docker run -td --name xtax xcorp/xtax:latest
docker ps
docker exec -ti xtax python CalcMyTax.py
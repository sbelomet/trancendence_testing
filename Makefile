# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mremenar <mremenar@42lausanne.ch>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/13 11:26:28 by lgosselk          #+#    #+#              #
#    Updated: 2024/11/16 12:06:19 by mremenar         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #


# -fsanitize=address -g3

# Variables
NAME		=	transcendence
ENTRY_PROD	=	./app/entrypoint.prod.sh
ENTRY_DEV	=	./app/entrypoint.sh

# Colors
RED 		=	\033[1;91m
YELLOW		=	\033[1;93m
GREEN		=	\033[1;92m
DEF_COLOR	=	\033[0;39m

# Commands
all:	$(NAME)

$(NAME):	pre
	@echo "$(GREEN) Starting production in detach $(DEF_COLOR)"
	@docker-compose -f docker-compose.prod.yml up -d --build
	@echo "$(YELLOW) Starting migrations $(DEF_COLOR)"
	@sleep 3
	docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
	@echo "$(YELLOW) Starting collectionStatic $(DEF_COLOR)"
	docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
	@echo "$(GREEN) Ready! $(DEF_COLOR)"

no_detach:
	@echo "$(GREEN) Starting production without detach $(DEF_COLOR)"
	@docker-compose -f docker-compose.prod.yml up --build
#	Manual migrations and collect statics
#	docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
#	docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear

dev:
	@echo "$(GREEN) Starting in dev $(DEF_COLOR)"
	@docker compose up --build

clean_dev:
	@docker-compose down -v
	@echo "$(RED) Removed! $(DEF_COLOR)"

clean_prod:
	@docker-compose -f docker-compose.prod.yml down -v
	@echo "$(RED) Removed! $(DEF_COLOR)"

fclean:
	@docker-system prune

pre:
	@chmod +x $(ENTRY_DEV)
	@chmod +x $(ENTRY_PROD)

.PHONY:			all clean_dev clean_prod fclean
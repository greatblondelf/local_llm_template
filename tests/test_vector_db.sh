#!/bin/bash

# fill up the vector DB:
../scripts_for_api_use/add_to_vector_db.sh example_username fix_this_put_in_a_real_auth_system localhost "This is a short document about frogs."
../scripts_for_api_use/add_to_vector_db.sh example_username fix_this_put_in_a_real_auth_system localhost "this is a similar short document but it is about tools and hardware."

# Then look for most-similar context:
../scripts_for_api_use/get_nn_vector_db.sh example_username fix_this_put_in_a_real_auth_system localhost "I just wanted to check that frogs are more similar to one of these."
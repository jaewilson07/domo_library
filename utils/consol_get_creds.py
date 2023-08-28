from ..DomoClasses import DomoAuth as dmda
from ..DomoClasses import DomoDataset as dmds
from .read_creds_from_dotenv import read_creds_from_dotenv, split_creds


def get_creds(array_env,
              array_key_starts_with,
              array_split,
              consol_env,
              consol_ds_id,
              debug: bool = False):
    instance_list = split_creds(env=array_env,
                                key_starts_with=array_key_starts_with,
                                env_var_list=array_split)

    if debug:
        print('\nconsol_env')
        print(consol_env, consol_env.CONSOL_INSTANCE)
        print('\ninstances to sync')
        for instance in instance_list:
            print(instance.domo_instance)

    consol_auth = dmda.DomoFullAuth(domo_instance=consol_env.CONSOL_INSTANCE,
                                    domo_username=consol_env.CONSOL_USERNAME,
                                    domo_password=consol_env.CONSOL_PASSWORD)

    consol_dataset = dmds.DomoDataset(full_auth=consol_auth, id=consol_ds_id)

    return instance_list, consol_auth, consol_dataset

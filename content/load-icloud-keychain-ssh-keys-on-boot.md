Title: Automatically Load SSH Keys from iCloud Keychain on Boot

You can add your SSH key into iCloud Keychain with the command below:

```sh
ssh-add --apple-use-keychain ~/.ssh/my-key
```

However, even after adding your SSH key to iCloud Keychain, your keys from there aren't going to be loaded automatically. At least this was the case for me.
You will have to run this command after every boot to load them and use the keys without typing any password:

```sh
ssh-add --apple-load-keychain
```

If you forget to run it, you will be prompted with a password by OpenSSH whenever you try to use the SSH key.

So the solution is simple. Just run the command on every boot automatically. While there are many ways to achieve this, I find creating an Automator application that runs that command, and adding it to the Login Items the best.
Open the Automator app (bundled with macOS). Choose the new application. Add the "Run Shell Script" action and enter the command below and save the Automator application.

```sh
ssh-add --apple-load-keychain
```

Finally, open macOS settings, and from **General > Login Items** add a new login item by clicking the plus (+) button and choosing the Automator application you've created.

I hope you find this useful.

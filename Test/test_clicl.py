import click

@click.command()
@click.option('--item', '-t', type=int)
def f(item):
    print ("{}".format(item/2))

if __name__ == '__main__':
    f()

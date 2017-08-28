import itertools
import configparser
from textwrap import dedent
from urllib.parse import urlparse

import click
import github
import pygraphviz as pgv


class CantExtractName(Exception):
    pass


def extract_submodule_name(url):
    if url.startswith('git@github.com:'):
        return url.split('git@github.com:')[1].split('.git')[0].strip('/')
    elif url.startswith('https://github.com') or url.startswith('git://github.com'):
        return urlparse(url).path[1:].split('.git')[0].strip('/')
    else:
        raise CantExtractName(url)


def iter_submodules(gh, repo):
    repo_name = repo.full_name

    try:
        raw_gitmodules = repo.get_file_contents('.gitmodules').decoded_content
    except github.UnknownObjectException:
        return

    gitmodules = raw_gitmodules.decode('utf-8')

    parser = configparser.RawConfigParser()
    parser.read_string(gitmodules)

    head = repo.get_commits()[0]

    for section_name in parser.sections():
        section = parser[section_name]
        url = section['url']
        path = section['path']

        try:
            submodule_name = extract_submodule_name(url)
        except CantExtractName:
            click.echo("Couldn't parse repo: %r" % url, err=True)
            continue

        try:
            sub_repo = gh.get_repo(submodule_name, lazy=False)
        except github.UnknownObjectException:
            click.echo("Can't find submodule %r" % submodule_name, err=True)
            continue

        sub_version = repo.get_file_contents(path).sha

        sub_head = sub_repo.get_commits()[0].sha

        comp = sub_repo.compare(sub_version, sub_head)

        yield repo_name, submodule_name, comp
        yield from iter_submodules(gh, sub_repo)


def resolve_repos(gh, orgs, repos):
    if not orgs and not repos:
        raise click.UsageError(
            "Must supply an org with --org or a repo with -r."
        )

    org_repos = list(itertools.chain.from_iterable(
        gh.get_organization(org).get_repos()
        for org in orgs
    ))
    repos = [gh.get_repo(repo) for repo in repos]
    return org_repos + repos


@click.option('-t', '--token',
              prompt=True,
              hide_input=True,
              envvar='GITHUB_API_TOKEN',
              help="GitHub Access Token")
@click.option('-r', '--repo', 'repos',
              multiple=True,
              help='Repository to include')
@click.option('-g', '--org', 'orgs',
              multiple=True,
              help="GitHub Organization to include")
@click.option('-o', '--output',
              default='repograph.svg',
              show_default=True,
              help="Output Path")
@click.option('-l', '--layout-program',
              default='dot',
              show_default=True,
              help="Program to use for rendering.")
@click.option('--strip-org/--no-strip-org',
              default=True,
              is_flag=True,
              help="Strip organization from node labels?")
@click.command(
    epilog=dedent(
        """\
        \b
        Examples:

        \b
        # Alternatively, you can pass the token via -t.
        $ export GITHUB_API_TOKEN=<token>

        \b
        # Draw a graph rooted at a single repo.
        $ python -m repograph -r <repo>

        \b
        # Draw a graph rooted with all the repos in an org.
        $ python -m repograph -o <org>
        """
    ),
)
def main(token,
         repos,
         orgs,
         output,
         layout_program,
         strip_org):
    """
    Draw a graph of GitHub submodule relationships.

    Specify roots of the repository graph with `-r <repo>` or `-o <org>`.

    Both -r and -o may be passed multiple times.
    """

    gh = github.Github(token)
    graph = pgv.AGraph(directed=True)

    repos = resolve_repos(gh, orgs, repos)

    for repo in repos:
        for source, dest, comp in iter_submodules(gh, repo):
            if strip_org:
                source = source.rsplit('/')[-1]
                dest = dest.rsplit('/')[-1]
            attrs = {}
            status = comp.status
            if status == 'ahead':
                attrs['label'] = "{} commits behind master.".format(
                    comp.total_commits)
                attrs['labelURL'] = comp.permalink_url
                attrs['labeltooltip'] = comp.permalink_url
                attrs['color'] = 'red'
            elif status == 'behind':
                attrs['label'] = 'Not on master.'
                attrs['labelURL'] = comp.permalink_url
                attrs['labeltooltip'] = comp.permalink_url
                attrs['color'] = 'red'
                attrs['style'] = 'dotted'
            graph.add_edge(source, dest, **attrs)

    if output.endswith('.dot'):
        print(graph, file=open(output, 'w'))
    else:
        graph.draw(output, prog=layout_program)

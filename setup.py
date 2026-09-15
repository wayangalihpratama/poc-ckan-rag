from setuptools import setup, find_namespace_packages

version = '0.1.0'

setup(
    name='ckanext-akvorag',
    version=version,
    description='CKAN extension for syncing document uploads with Akvo RAG Knowledge Base',
    long_description='''Automated event-driven synchronization between CKAN datasets/resources and Akvo RAG platform.''',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='CKAN RAG Akvo Knowledgebase AI',
    author='Akvo Team',
    author_email='dev@akvo.org',
    url='https://github.com/wayangalihpratama/poc-ckan-rag',
    license='Apache License 2.0',
    packages=find_namespace_packages(include=['ckanext', 'ckanext.*']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests>=2.28.0',
        'click>=8.0.0',
    ],
    entry_points='''
        [ckan.plugins]
        akvorag=ckanext.akvorag.plugin:AkvoRAGPlugin

        [ckan.cli]
        akvorag=ckanext.akvorag.cli:akvorag
    ''',
)

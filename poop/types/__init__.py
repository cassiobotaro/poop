"""POOP's type wrappers, one module per wrapped builtin.

Import from the module that defines a name. Nothing is re-exported here: a
package `__init__` runs before any submodule, so a list here would load the
whole type tree, in its own order, for every import of any one of them.
"""

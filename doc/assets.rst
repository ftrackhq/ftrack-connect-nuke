..
    :copyright: Copyright (c) 2015 ftrack

###############
Managing assets
###############

Importing assets
================

Assets can be imported into Nuke from the Import Asset pane.

.. image:: /image/import_asset_pane.jpg

The pane can be opened from the ftrack menu:

.. image:: /image/ftrack_menu_import_asset_menu_option.jpg

1. Browse to a shot using the :menuselection:`Import from` button. Your current
   shot will be preselected.
2. Select an asset with corresponding version.
3. Click :menuselection:`Import` on a component to add a read node to the script
   reading that components path.

Managing assets
===============

The asset manager can be used to keep track of your existing assets in your
script.

.. image:: /image/asset_manager_pane.png

It can be opened from the ftrack menu:

.. image:: /image/ftrack_menu_asset_manager_menu_option.png

From the asset manager you can quickly see what assets are on the latest version
(green) and quickly update all assets to the latest version by selecting all of
them and clicking the :menuselection:`Latest` button.

You can also remove an asset from the script or select it in your node graph.

Publishing assets
=================

To publish a rendered image sequence from Nuke, add a ftrack publish node after
it.

.. image:: /image/publish_node.png

To publish the image sequence as a new version, either select an existing asset
or create a new one by giving it a name.

.. image:: /image/publish_pane.png

These options are available when publishing:

:Copy files:            Publish will copy the files to another location and publish them
                        from there.
:Attach Nuke script:    Attaches the Nuke script as a component on the published
                        version.

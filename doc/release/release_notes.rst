..
    :copyright: Copyright (c) 2015 ftrack

.. _release/release_notes:


*************
Release notes
*************

.. release:: 1.2.1
    :date: 2019-07-10

    .. change:: fix

        Fix QStringListModel compatibility for PySide2 5.9+.


.. release:: 1.2.0
    :date: 2018-12-19

    .. change:: changed
        :tags: Internal

        Convert code to standalone ftrack-connect plugin.

.. release:: 1.1.5
    :date: 2018-10-11

    .. change:: changed
        :tags: Ui

        Update Icon.

    .. change:: fixed
        :tags: Nuke

        Asset Info occassionaly breaks on selection items that are not nodes.

.. release:: 1.1.4
    :date: 2018-04-27

    .. change:: fixed
        :tags: Nuke

        Asset Info does not display correct informations.

    .. change:: fixed
        :tags: API

        Not all the code has been ported to PySide2.

    .. change:: changed
        :tags: Crew

        Remove Crew widget chat and notifications.

    .. change:: fixed
        :tags: Nuke

        Nuke does not correctly set frame range on startup.

    .. change:: fixed
        :tags: Assets

        Support for importing all assets multiple times.

.. release:: 1.1.3

    :date: 2018-01-09

    .. change:: fix
       :tags: Logging

       Make sure usage module is imported in the main module
       to avoid issues with cx-freeze imports.

.. release:: 1.1.2

    :date: 2017-12-14

    .. change:: new
       :tags: Logging

       Improved feedback gathering.

   .. change:: fixed

      On import set the node color to signify if it is the
      latest version or not.

.. release:: 1.1.1

    :date: 2017-11-16

   .. change:: new
       :tags: Nuke Assist

       Nuke Assist is now available as a lunchable
       application.

.. release:: 1.1.0
    :date: 2017-09-12

    .. change:: fixed
        :tags: Nuke

        Nuke 11 is not supported.

.. release:: 1.0.1
  :date: 2017-07-11

  .. change:: fixed
        :tags: Actions

        Nuke is discovered under NukeStudio in Connect.

.. release:: 1.0.0
  :date: 2017-07-07

    .. change:: fixed
        :tags: Gizmo, Assets

        Import may fail for Windows paths with backslashes.

  .. change:: changed
        :tags: Internal

        Gizmo publisher is not using new api.

  .. change:: fixed
        :tags: API

        Connector does not get initialized correctly.

  .. change:: fixed
        :tags: API

        NukeX does not get properly discovered under OSx.

.. release:: 0.1.13
    :date: 2017-01-04

    .. change:: fixed
        :tags: Ui

        Nuke has two tabs called ftrack.

    .. change:: fixed
        :tags: Asset

        Render asset cannot be versioned.

    .. change:: changed
        :tags: Documentation

        Added :ref:`getting_started` instructions.

.. release:: 0.1.12
    :date: 2016-12-06

    .. change:: changed
        :tags: Internal

        Switched to use Connect > 0.1.32.

.. release:: 0.1.11
    :date: 2016-12-01

    .. change:: changed
        :tags: API

        Switched to require ftrack-python-api > 1.0.0.

.. release:: 0.1.10
    :date: 2016-12-01

    .. change:: fixed
        :tags: API, Assets

        Scanning for new asset versions at scene startup is very slow.

    .. change:: fixed
        :tags: User interface

        Nuke does not allow to change version of imported almebic.

.. release:: 0.1.9
    :date: 2016-09-16

    .. change:: fixed
        :tags: Hook

        Launch hook is registered twice.

    .. change:: fixed
        :tags: Ui

        Nuke raise an error while trying to reload a previously published
        script.

    .. change:: fixed
        :tags: Publish

        Components in publish node appears to be editable but are not.

.. release:: 0.1.8
    :date: 2016-06-07

    .. change:: fixed
        :tags: Ui

        The load script / publish menu entries script are broken.

    .. change:: fixed
        :tags: Ui

        Closing Nuke while gizmo publisher is open causes segmentation fault.

.. release:: 0.1.7
    :date: 2016-05-02

    .. change:: changed
        :tags: Publish

        Update text on publish node knob from `copy files` to `force copy files`
        and add tooltip.

    .. change:: fixed

        Importing `ftrack_connect_nuke` module without
        `QtGui.QApplication <https://srinikom.github.io/pyside-docs/PySide/QtGui/QApplication.html>`_
        causes segmentation fault.

.. release:: 0.1.6
    :date: 2015-09-22

    .. change:: fixed

        Non-commercial NukeX appears as regular NukeX when started from
        actions.

.. release:: 0.1.5
    :date: 2015-09-08

    .. change:: new
        :tags: Crew

        Added support for crew chat and in-app notifications.

.. release:: 0.1.4

    .. change:: new
        :tags: Publish

        Added support for publishing other render types than image sequences.
        This requires a new asset type on the ftrack server. :ref:`Read more <release/migration/next/new_render_asset_type>`

.. release:: 0.1.3
    :date: 2015-04-17

    .. change:: fix
        :tags: Hook, Centos

        Added support for launching plugin on Centos.

.. release:: 0.1.2
    :date: 2015-03-18

    .. change:: new
        :tags: Gizmo, Assets

        Gizmo publish and import from Nuke.

    .. change:: new
        :tags: User interface

        Updated style in dialogs and improved feedback.

.. release:: 0.1.1
    :date: 2015-03-02

    .. change:: fix
        :tags: User interface

        Plugin errors when objects and files have non-ascii characters.

.. release:: 0.1.0
    :date: 2015-02-19

    .. change:: changed
        :tags: User interface

        Added information panes to ftrack menu.
